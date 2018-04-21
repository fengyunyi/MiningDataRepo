// ERC20: https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/token/ERC20/StandardToken.sol

// In solidity allowance is defined as mapping type:
// mapping (address => mapping (address => uint256)) allowance

// Note that "Mappings can be seen as hash tables which are virtually initialized 
// such that every possible key exists and is mapped to a value whose byte-representation is 
// all zeros: a type’s default value. The similarity ends here, though: The key data is not 
// actually stored in a mapping, only its keccak256 hash used to look up the value."

open util/ordering[ERC20] as ord
sig Address{} // either externally owned accounts (EOA) or contracts

sig ERC20{
	totalSupply: one Int, // in the smallest, nondividable unit
	balance: Address -> one Int,

	// not sure
	spenderAllowed: Address -> one Int,
	allowance: Address -> spenderAllowed,
	}


// msg.sender(fromAddr) sends $value to another address (to_address)
pred transfer(toAddr, fromAddr: Address,  t, t': ERC20, value: Int){
	// preconditions
	value =< t.balance[fromAddr]
	
	// copy unchanged relations
	t'.totalSupply = t.totalSupply
	t'.allowance = t.allowance
	
	// Apply the transition
	let fromBal = t.balance[fromAddr] |
	let toBal = t.balance[toAddr] |
		t'.balance = t.balance ++ (fromAddr -> minus[fromBal, value])
		&& t'.balance = t.balance ++ (toAddr -> plus[toBal, value])
}

// allow spender (expecting a contract but could be EOA) to withdraw from user's account, multiple times, up to the _value amount
// the spendable amount is min(balance, allowance) of a user account
// msg.sender is user
pred approve(spender, user: Address, t, t': ERC20, value: Int){

	// copy unchanged relations
	t'.totalSupply = t.totalSupply
	t'.balance = t.balance

	// not sure (user may not be in allowance)
	t'.allowance = t.allowance ++ (user -> spender -> value)
}

// This is meant to be used with approve
// spender (msg.sender): expecting a contract (but can be called by EOA?)
// spender transfers $value fromAddr to toAddr as long as allowance[fromAddr][spender]>= value
// This function and aprove enable the scenario where a contract executes upon the payment of someone
pred transferFrom(spender, toAddr, fromAddr: Address, t, t': ERC20, value: Int){
	// preconditions
	value =< t.balance[fromAddr]
	value =< t.allowance[fromAddr][spender]

	// copy unchanged relations
	t'.totalSupply = t.totalSupply

	// not sure
	let fromBal = t.balance[fromAddr] |
		t'.balance = t.balance ++ (fromAddr -> minus[fromBal, value])
	let toBal = t.balance[toAddr] |
		t'.balance = t.balance ++ (toAddr -> plus[toBal, value])
	let fromAllowed = t.allowance[fromAddr][spender] |
		t'.allowance = t.allowance ++ (fromAddr -> spender -> minus[fromAllowed, value])
}


// newly created ERC20 token by msg.sender
pred freshERC20(sender: Address, supply: Int, token: ERC20) {
	token.totalSupply = supply
	all a: Address | token.balance[a] = 0
	all a, b: Address | token.allowance[a][b] = 0  // not sure
	token.balance[sender] = supply  // all tokens belongs to the creator at the beginning, is this true?
}

// states of the token
fact traces {
	// the first state is a freshly created token
	some creator: Address, sup: Int | freshERC20[creator, sup, ord/first]

	all ts: ERC20 - ord/last | // for all token states except the last
		let ts' = ts.next | // the next state satisfies
			(some sender, recipiant: Address, val: Int | transfer[recipiant, sender, ts, ts', val])
			or (some spender, caller: Address, val: Int | approve[spender, caller, ts, ts', val])
			or (some spender, sender, recipiant: Address, val: Int | transferFrom[spender, sender, recipiant, ts, ts', val])
}


// assertions

// total balance == totalSupply should always hold
assert totalBalance {
	all token: ERC20 |
		token.totalSupply = (sum b: Address | token.balance[b])
}
	
	
// scope: 2 ERC20 tokens and 8 Addresses
check totalBalance for 2 but 8 Address
